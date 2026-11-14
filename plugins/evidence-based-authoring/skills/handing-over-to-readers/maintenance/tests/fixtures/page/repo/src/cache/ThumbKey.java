package cache;

import java.util.Objects;

/**
 * The cache key of one picture's thumbnail.
 */
public final class ThumbKey {

    private final long pictureId;
    private final int version;

    public ThumbKey(long pictureId, int version) {
        this.pictureId = pictureId;
        this.version = version;
    }

    public long pictureId() {
        return pictureId;
    }

    public String value() {
        return "thumb:" + pictureId + ":v" + version;
    }

    @Override
    public boolean equals(Object other) {
        return other instanceof ThumbKey key && key.pictureId == pictureId && key.version == version;
    }

    @Override
    public int hashCode() {
        return Objects.hash(pictureId, version);
    }
}
